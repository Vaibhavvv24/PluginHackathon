import React from "react";

const Home = () => {
  return (
    <div className="bg-gray-100 min-h-screen">
      <header className="bg-blue-500 text-white py-10">
        <div className="container mx-auto text-center">
          <h1 className="text-4xl font-bold">
            Welcome to AI English Communication Assessment
          </h1>
          <p className="mt-4 text-lg">
            Enhance your English communication skills with AI-driven insights
            and assessments.
          </p>
        </div>
      </header>

      <main className="container mx-auto my-10">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Card 1 */}
          <div className="bg-white shadow-lg rounded-lg p-6 text-center">
            <h2 className="text-xl font-semibold mb-4">Take Assessment</h2>
            <p>
              Start your assessment and receive personalized feedback on your
              communication skills.
            </p>
            <button className="mt-4 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-700">
              Start Now
            </button>
          </div>

          {/* Card 2 */}
          <div className="bg-white shadow-lg rounded-lg p-6 text-center">
            <h2 className="text-xl font-semibold mb-4">View Your History</h2>
            <p>
              Access your previous assessments and track your improvement over
              time.
            </p>
            <button className="mt-4 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-700">
              View History
            </button>
          </div>

          {/* Card 3 */}
          <div className="bg-white shadow-lg rounded-lg p-6 text-center">
            <h2 className="text-xl font-semibold mb-4">Personalized Profile</h2>
            <p>
              Manage your profile and get tailored recommendations to boost your
              skills.
            </p>
            <button className="mt-4 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-700">
              Go to Profile
            </button>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Home;
