import React, { useRef, useState } from "react";
import { FFmpeg } from "@ffmpeg/ffmpeg";
import { fetchFile } from "@ffmpeg/util";
import axios from "axios";

const Video = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [videoUrl, setVideoUrl] = useState(null);
  const [mp3Url, setMp3Url] = useState(null);
  const [loading, setLoading] = useState(false);

  const videoRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const recordedChunks = useRef([]);
  const ffmpeg = new FFmpeg();

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

  const convertToMp3 = async () => {
    if (!videoUrl) {
      alert("No video recorded!");
      return;
    }

    setLoading(true);
    console.log(videoUrl);

    await ffmpeg.load();

    // Fetch and write video file to FFmpeg
    const response = await fetch(videoUrl);
    console.log(response);
    const videoBlob = await response.blob();
    console.log(videoBlob);
    await ffmpeg.writeFile("input.mp4", await fetchFile(videoBlob));

    // Convert MP4 to MP3
    await ffmpeg.exec(["-i", "input.mp4", "output.mp3"]);
    console.log("Conversion complete!");
    // Read and create MP3 file URL
    const mp3File = await ffmpeg.readFile("output.mp3");
    console.log(mp3File);
    const mp3Blob = new Blob([mp3File.buffer], { type: "audio/mp3" });
    const mp3Url = URL.createObjectURL(mp3Blob);

    setMp3Url(mp3Url);
    setLoading(false);

    // Optionally upload the MP3
    uploadMp3(mp3Blob);
  };

  const uploadMp3 = async (mp3Blob) => {
    const formData = new FormData();
    formData.append("file", mp3Blob, "audio.mp3");

    try {
      const response = await axios.post(
        "http://your-backend-endpoint/upload",
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );
      alert("MP3 uploaded successfully!");
    } catch (error) {
      console.error("Error uploading MP3:", error);
      alert("Failed to upload MP3.");
    }
  };

  return (
    <div>
      <h1>Live Video Recorder</h1>
      <video
        ref={videoRef}
        autoPlay
        playsInline
        style={{ width: "500px", height: "300px" }}
      ></video>
      <br />
      {!isRecording && (
        <button onClick={startRecording}>Start Recording</button>
      )}
      {isRecording && <button onClick={stopRecording}>Stop Recording</button>}
      {videoUrl && (
        <div>
          <h3>Recorded Video:</h3>
          <video
            src={videoUrl}
            controls
            style={{ width: "500px", height: "300px" }}
          ></video>
          <button onClick={convertToMp3} disabled={loading}>
            {loading ? "Converting to MP3..." : "Convert to MP3"}
          </button>
        </div>
      )}
      {mp3Url && (
        <div>
          <h3>MP3 Preview:</h3>
          <audio src={mp3Url} controls></audio>
          <a href={mp3Url} download="audio.mp3">
            Download MP3
          </a>
        </div>
      )}
    </div>
  );
};

export default Video;
