import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const Assessment = () => {
  const navigate = useNavigate();

  const questions = [
    "Tell us about yourself?",
    "What’s your view on remote work culture?",
    "How do you stay updated with industry trends?",
    "What inspired you to choose your career path?",
    "What are your strengths and weaknesses?",
    "Where do you see yourself in five years?",
    "Can you describe a challenging situation and how you overcame it?",
    "What do you consider your greatest professional achievement?",
    "How do you handle criticism or feedback?",
    "What motivates you in your work?",
    "What role does teamwork play in your professional success?",
    "How do you prioritize tasks during busy periods?",
    "Can you share an example of when you demonstrated leadership skills?",
    "How do you handle conflicts with colleagues?",
    "What steps do you take to ensure professional growth?",
    "What are the most important skills for your career?",
    "How do you prepare for big projects or presentations?",
    "What’s your approach to time management?",
    "What do you think about the importance of networking?",
    "Can you share a time when you had to learn something quickly?",
    "How do you balance personal and professional life?",
    "What do you value most in a workplace environment?",
    "How do you approach decision-making under pressure?",
    "What’s your take on lifelong learning?",
    "How do you handle multiple projects with competing deadlines?",
    "What is your approach to self-improvement?",
    "What inspires you to stay motivated daily?",
    "Can you discuss a time when you went above and beyond?",
    "What do you enjoy most about your current role?",
    "How do you ensure clear communication in a team?",
    "What’s your process for setting and achieving goals?",
    "What advice would you give to someone starting in your field?",
    "How do you adapt to changes in your industry?",
    "Can you share a time you failed and how you handled it?",
    "What role does technology play in your work?",
    "What qualities do you believe are necessary for success?",
    "How do you handle constructive feedback from peers?",
    "What’s your take on work-life balance?",
    "Can you share an example of innovative thinking in your work?",
    "How do you approach skill development?",
    "What makes a great leader in your opinion?",
    "How do you manage stress during tight deadlines?",
    "What’s your opinion on professional mentorship?",
    "What’s the most impactful lesson you’ve learned in your career?",
    "How do you foster creativity in your work?",
    "What is your approach to overcoming obstacles?",
    "How do you evaluate your performance over time?",
    "What’s your vision for the future of your field?",
  ];

  const [currentQuestion, setCurrentQuestion] = useState(
    questions[Math.floor(Math.random() * questions.length)]
  );

  const handleNextQuestion = () => {
    const newQuestion = questions[Math.floor(Math.random() * questions.length)];
    setCurrentQuestion(newQuestion);
  };

  return (
    <div className="bg-blue-50 min-h-screen flex flex-col items-center p-5">
      <h1 className="text-4xl font-bold text-blue-700 mt-10 mb-6">
        Take Assessment
      </h1>
      <div className="bg-white shadow-lg rounded-lg p-8 max-w-3xl w-full">
        <h2 className="text-2xl text-gray-800 text-center font-semibold mb-6">
          {currentQuestion}
        </h2>
        <div className="flex justify-between">
          <button
            onClick={handleNextQuestion}
            className="bg-blue-700 text-white p-3 rounded-lg hover:bg-blue-800"
          >
            Next Question
          </button>
          <button
            onClick={() => navigate("/video")}
            className="bg-blue-700 text-white p-3 rounded-lg hover:bg-blue-800"
          >
            Go to Video Page
          </button>
        </div>
      </div>
    </div>
  );
};

export default Assessment;
