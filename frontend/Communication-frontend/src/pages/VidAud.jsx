import React, { useState } from "react";
import VideoToAudio from "video-to-audio";

function VidAud() {
  const [audioData, setAudioData] = useState(null);

  // Function to handle video file input change
  const handleFileChange = async (event) => {
    const sourceVideoFile = event.target.files[0];
    const targetAudioFormat = "mp3";

    try {
      const convertedAudioDataObj = await VideoToAudio.convert(
        sourceVideoFile,
        targetAudioFormat
      );
      setAudioData(convertedAudioDataObj);
    } catch (error) {
      console.error("Error converting video to audio:", error);
    }
  };

  // Function to handle audio file download
  const downloadAudio = () => {
    if (audioData) {
      const a = document.createElement("a");
      a.href = audioData.data;
      a.download = `${audioData.name}.${audioData.format}`;
      a.click();
    }
  };

  return (
    <div>
      <input
        type="file"
        accept=".mp4, .avi, .mov"
        onChange={handleFileChange}
      />
      {audioData && (
        <div>
          <button onClick={downloadAudio}>Download Audio</button>
        </div>
      )}
    </div>
  );
}

export default VidAud;
