import { useEffect, useEffectEvent, useRef, useState } from 'react'
import { useParams } from 'react-router-dom'
import { InlineError, SplashScreen, StatusPill } from '../components/UI'
import { apiRequest } from '../lib/api'
import { formatDateTime } from '../lib/formatters'
import { useApiResource } from '../lib/useApiResource'

export function MeetingRoom({ token, session }) {
  const { appointmentId } = useParams()
  const { data: appointment, loading, error, refetch } = useApiResource(
    `/api/appointments/${appointmentId}/`,
    token,
    null,
  )
  const localVideoRef = useRef(null)
  const remoteVideoRef = useRef(null)
  const peerRef = useRef(null)
  const localStreamRef = useRef(null)
  const pendingCandidatesRef = useRef([])
  const lastSignalIdRef = useRef(0)
  const [mediaReady, setMediaReady] = useState(false)
  const [callState, setCallState] = useState('idle')
  const [activity, setActivity] = useState('Open camera first, then launch the room.')

  async function sendSignal(kind, payload = {}) {
    await apiRequest(`/api/appointments/${appointmentId}/signals/`, {
      method: 'POST',
      token,
      body: { kind, payload },
    })
  }

  function ensurePeerConnection() {
    if (peerRef.current) {
      return peerRef.current
    }

    const peer = new RTCPeerConnection({
      iceServers: [{ urls: 'stun:stun.l.google.com:19302' }],
    })

    peer.onicecandidate = (event) => {
      if (event.candidate) {
        sendSignal('candidate', { candidate: event.candidate.toJSON() })
      }
    }

    peer.ontrack = (event) => {
      const [remoteStream] = event.streams
      if (remoteVideoRef.current) {
        remoteVideoRef.current.srcObject = remoteStream
      }
      setCallState('connected')
      setActivity('Remote stream connected.')
    }

    peer.onconnectionstatechange = () => {
      if (peer.connectionState === 'connected') {
        setCallState('connected')
      }
      if (peer.connectionState === 'failed' || peer.connectionState === 'disconnected') {
        setCallState('disconnected')
      }
    }

    peerRef.current = peer
    return peer
  }

  function attachLocalTracks(peer, stream) {
    const existingTrackIds = new Set(
      peer
        .getSenders()
        .map((sender) => sender.track?.id)
        .filter(Boolean),
    )

    stream.getTracks().forEach((track) => {
      if (!existingTrackIds.has(track.id)) {
        peer.addTrack(track, stream)
      }
    })
  }

  async function flushPendingCandidates(peer) {
    while (pendingCandidatesRef.current.length) {
      const candidate = pendingCandidatesRef.current.shift()
      await peer.addIceCandidate(candidate)
    }
  }

  async function enableMedia() {
    if (localStreamRef.current) {
      return
    }

    const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true })
    localStreamRef.current = stream

    if (localVideoRef.current) {
      localVideoRef.current.srcObject = stream
    }

    const peer = ensurePeerConnection()
    attachLocalTracks(peer, stream)
    setMediaReady(true)
    setActivity('Camera and microphone are ready.')
    await sendSignal('ready', { role: session.user.role })
  }

  async function startCall() {
    await enableMedia()
    const peer = ensurePeerConnection()
    const offer = await peer.createOffer()
    await peer.setLocalDescription(offer)
    await sendSignal('offer', { type: offer.type, sdp: offer.sdp })
    setCallState('calling')
    setActivity('Offer sent. Waiting for the other side to join.')
    if (session.user.role === 'doctor') {
      await apiRequest(`/api/appointments/${appointmentId}/status/`, {
        method: 'PATCH',
        token,
        body: { status: 'live' },
      })
      refetch()
    }
  }

  async function processSignal(signal) {
    if (signal.kind === 'ready') {
      setActivity('The other participant opened their media.')
      return
    }

    if (signal.kind === 'end') {
      teardownCall(false)
      setActivity('The other participant ended the session.')
      setCallState('ended')
      return
    }

    if (signal.kind === 'offer' && session.user.role === 'patient') {
      await enableMedia()
      const peer = ensurePeerConnection()
      await peer.setRemoteDescription(new RTCSessionDescription(signal.payload))
      await flushPendingCandidates(peer)
      const answer = await peer.createAnswer()
      await peer.setLocalDescription(answer)
      await sendSignal('answer', { type: answer.type, sdp: answer.sdp })
      setCallState('connecting')
      setActivity('Answer sent back to the doctor.')
      return
    }

    if (signal.kind === 'answer' && session.user.role === 'doctor') {
      const peer = ensurePeerConnection()
      await peer.setRemoteDescription(new RTCSessionDescription(signal.payload))
      await flushPendingCandidates(peer)
      setCallState('connecting')
      setActivity('Answer received. Negotiating connection.')
      return
    }

    if (signal.kind === 'candidate' && signal.payload?.candidate) {
      const peer = ensurePeerConnection()
      const candidate = new RTCIceCandidate(signal.payload.candidate)
      if (peer.remoteDescription) {
        await peer.addIceCandidate(candidate)
      } else {
        pendingCandidatesRef.current.push(candidate)
      }
    }
  }

  async function teardownCall(sendEnd = true) {
    if (sendEnd) {
      try {
        await sendSignal('end', {})
      } catch {
        // Ignore send-end failures in local testing.
      }
    }

    if (peerRef.current) {
      peerRef.current.close()
      peerRef.current = null
    }
    if (localStreamRef.current) {
      localStreamRef.current.getTracks().forEach((track) => track.stop())
      localStreamRef.current = null
    }
    if (localVideoRef.current) {
      localVideoRef.current.srcObject = null
    }
    if (remoteVideoRef.current) {
      remoteVideoRef.current.srcObject = null
    }
    pendingCandidatesRef.current = []
    setMediaReady(false)
    setCallState('ended')
  }

  const processPolledSignal = useEffectEvent(async (signal) => {
    await processSignal(signal)
  })

  const cleanupRoom = useEffectEvent(() => {
    teardownCall(false)
  })

  useEffect(() => {
    if (!appointmentId || !token) {
      return undefined
    }

    let ignore = false

    async function pollSignals() {
      try {
        const signals = await apiRequest(
          `/api/appointments/${appointmentId}/signals/?after=${lastSignalIdRef.current}`,
          { token },
        )
        for (const signal of signals) {
          if (ignore) {
            return
          }
          lastSignalIdRef.current = signal.id
          await processPolledSignal(signal)
        }
      } catch {
        // Keep polling resilient for local testing.
      }
    }

    const intervalId = window.setInterval(pollSignals, 1200)
    pollSignals()

    return () => {
      ignore = true
      window.clearInterval(intervalId)
      cleanupRoom()
    }
  }, [appointmentId, token])

  if (loading && !appointment) {
    return <SplashScreen />
  }

  if (error && !appointment) {
    return <InlineError error={error} retry={refetch} />
  }

  return (
    <div className="page-shell">
      <section className="hero-panel">
        <div>
          <span className="eyebrow">Local WebRTC</span>
          <h1>{appointment.concern}</h1>
          <p>
            Test this locally with two tabs or two browsers. Doctor launches the call, patient joins
            the same appointment room.
          </p>
        </div>
        <div className="header-badges">
          <StatusPill value={appointment.status} />
          <StatusPill value={callState} />
        </div>
      </section>

      <section className="meeting-layout">
        <section className="panel wide">
          <div className="video-grid">
            <div className="video-card">
              <span className="eyebrow">You</span>
              <video ref={localVideoRef} autoPlay muted playsInline />
            </div>
            <div className="video-card">
              <span className="eyebrow">Remote</span>
              <video ref={remoteVideoRef} autoPlay playsInline />
            </div>
          </div>

          <div className="card-actions">
            <button type="button" className="secondary-button" onClick={enableMedia} disabled={mediaReady}>
              {mediaReady ? 'Camera ready' : 'Enable camera'}
            </button>
            {session.user.role === 'doctor' ? (
              <button type="button" className="primary-button" onClick={startCall}>
                Launch call
              </button>
            ) : (
              <button type="button" className="primary-button" onClick={enableMedia}>
                Ready to join
              </button>
            )}
            <button type="button" className="ghost-button" onClick={() => teardownCall(true)}>
              End session
            </button>
          </div>
        </section>

        <section className="panel">
          <div className="section-head">
            <div>
              <span className="eyebrow">Live brief</span>
              <h2>PulseMatch summary</h2>
            </div>
          </div>
          <p>{appointment.copilot_summary}</p>
          <ul className="checklist">
            {appointment.copilot_checklist.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
          <div className="room-details">
            <div>
              <span>Meeting code</span>
              <strong>{appointment.meeting_code}</strong>
            </div>
            <div>
              <span>Appointment</span>
              <strong>{formatDateTime(appointment.starts_at)}</strong>
            </div>
            <div>
              <span>Activity</span>
              <strong>{activity}</strong>
            </div>
          </div>
        </section>
      </section>
    </div>
  )
}
