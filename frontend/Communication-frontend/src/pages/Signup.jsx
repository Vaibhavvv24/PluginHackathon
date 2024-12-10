import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

const Signup = () => {
  const [formData, setFormData] = useState({});
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.id]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const res = await fetch("http://127.0.0.1:8000/register-user/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(formData),
    });
    const data = await res.json();
    console.log(data);
    navigate("/login");
  };

  return (
    <div className="bg-blue-50 min-h-screen flex flex-col items-center p-5">
      <h1 className="text-4xl font-bold text-blue-700 mt-10">Sign Up</h1>
      <form
        className="bg-white shadow-lg rounded-lg p-8 mt-6 w-full max-w-md flex flex-col gap-6"
        onSubmit={handleSubmit}
      >
        <input
          type="text"
          placeholder="Name"
          id="username"
          className="border border-blue-300 p-3 rounded-lg focus:outline-none focus:ring focus:ring-blue-200"
          onChange={handleChange}
        />
        <input
          type="email"
          placeholder="Email"
          id="email"
          className="border border-blue-300 p-3 rounded-lg focus:outline-none focus:ring focus:ring-blue-200"
          onChange={handleChange}
        />
        <input
          type="password"
          placeholder="Password"
          id="password"
          className="border border-blue-300 p-3 rounded-lg focus:outline-none focus:ring focus:ring-blue-200"
          onChange={handleChange}
        />
        <button
          type="submit"
          className="bg-blue-700 text-white p-3 rounded-lg uppercase hover:bg-blue-800"
        >
          Sign Up
        </button>
      </form>
      <p className="mt-4 text-sm">
        Already have an account?{" "}
        <Link to="/login" className="text-blue-700 hover:underline">
          Login
        </Link>
      </p>
    </div>
  );
};

export default Signup;
