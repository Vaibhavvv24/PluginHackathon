import React, { useRef, useState } from "react";
import axios from "axios";
import * as lamejs from "@breezystack/lamejs";

const Video = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [videoUrl, setVideoUrl] = useState(null);
  const [mp3Url, setMp3Url] = useState(null);
  const [loading, setLoading] = useState(false);

  const videoRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const recordedChunks = useRef([]);

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: true,
      audio: true,
    });
    videoRef.current.srcObject = stream;

    mediaRecorderRef.current = new MediaRecorder(stream);
    mediaRecorderRef.current.ondataavailable = (event) => {
      if (event.data.size > 0) {
        recordedChunks.current.push(event.data);
      }
    };

    mediaRecorderRef.current.onstop = () => {
      const blob = new Blob(recordedChunks.current, { type: "video/mp4" });
      const url = URL.createObjectURL(blob);
      setVideoUrl(url);
    };

    recordedChunks.current = [];
    mediaRecorderRef.current.start();
    setIsRecording(true);
  };

  const stopRecording = () => {
    mediaRecorderRef.current.stop();
    const tracks = videoRef.current.srcObject.getTracks();
    tracks.forEach((track) => track.stop());
    setIsRecording(false);
  };

  const convertToMp3WithoutFFmpeg = async () => {
    if (!videoUrl) {
      alert("No video recorded!");
      return;
    }

    setLoading(true);

    try {
      const videoBlob = await fetch(videoUrl).then((response) =>
        response.blob()
      );

      // Decode audio from video blob
      const audioContext = new AudioContext();
      const arrayBuffer = await videoBlob.arrayBuffer();
      const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

      // Debug: Check the audio buffer's information
      console.log("Audio buffer info:", audioBuffer);

      const mp3Encoder = new lamejs.Mp3Encoder(
        1, // Mono (1 channel)
        audioBuffer.sampleRate, // Input sample rate
        128 // Bitrate in kbps
      );

      const samples = audioBuffer.getChannelData(0); // Get left channel audio samples
      const mp3Chunks = [];
      const sampleBlockSize = 1152; // Block size for encoding

      for (let i = 0; i < samples.length; i += sampleBlockSize) {
        const sampleChunk = samples.subarray(i, i + sampleBlockSize);
        const mp3Chunk = mp3Encoder.encodeBuffer(sampleChunk);

        if (mp3Chunk.length > 0) {
          mp3Chunks.push(mp3Chunk);
        }
      }

      const mp3FinalChunk = mp3Encoder.flush();
      if (mp3FinalChunk.length > 0) {
        mp3Chunks.push(mp3FinalChunk);
      }

      // Create MP3 blob
      const mp3Blob = new Blob(mp3Chunks, { type: "audio/mp3" });

      // Debug: Check the mp3Blob size
      console.log("MP3 Blob size:", mp3Blob.size);

      const mp3Url = URL.createObjectURL(mp3Blob);
      setMp3Url(mp3Url); // Set the URL to state for rendering
    } catch (error) {
      console.error("Error during MP3 conversion:", error);
      alert("An error occurred while converting to MP3.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-blue-50 min-h-screen flex flex-col items-center p-6">
      <h1 className="text-4xl font-bold text-blue-700 mt-6 mb-4">
        Live Video Recorder
      </h1>
      <video
        ref={videoRef}
        autoPlay
        playsInline
        className="w-full max-w-lg rounded shadow-md border border-blue-300"
      ></video>
      <div className="mt-6 flex gap-4">
        {!isRecording && (
          <button
            onClick={startRecording}
            className="bg-blue-700 text-white px-6 py-3 rounded-lg hover:bg-blue-800 shadow-md"
          >
            Start Recording
          </button>
        )}
        {isRecording && (
          <button
            onClick={stopRecording}
            className="bg-red-600 text-white px-6 py-3 rounded-lg hover:bg-red-700 shadow-md"
          >
            Stop Recording
          </button>
        )}
      </div>
      {videoUrl && (
        <div className="mt-8 w-full max-w-lg">
          <h3 className="text-xl font-semibold text-blue-700 mb-4">
            Recorded Video:
          </h3>
          <video
            src={videoUrl}
            controls
            className="w-full max-w-lg rounded shadow-md border border-blue-300"
          ></video>
          <div className="mt-4">
            <a
              href={videoUrl}
              download="video.mp4"
              className="inline-block bg-blue-700 text-white px-6 py-3 rounded-lg hover:bg-blue-800 shadow-md"
            >
              Download MP4
            </a>
          </div>
          <button onClick={convertToMp3WithoutFFmpeg} disabled={loading}>
            {loading ? "Converting to MP3..." : "Convert to MP3"}
          </button>
        </div>
      )}
      {mp3Url && (
        <div className="mt-8 w-full max-w-lg">
          <h3 className="text-xl font-semibold text-blue-700 mb-4">
            MP3 Preview:
          </h3>
          <audio
            src={mp3Url}
            controls
            className="w-full rounded shadow-md border border-blue-300"
          ></audio>
          <a
            href={mp3Url}
            download="audio.mp3"
            className="mt-4 inline-block bg-blue-700 text-white px-6 py-3 rounded-lg hover:bg-blue-800 shadow-md"
          >
            Download MP3
          </a>
        </div>
      )}
    </div>
  );
};

export default Video;
