import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";

const Login = () => {
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
    const res = await fetch("http://127.0.0.1:8000/token/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(formData),
    });
    const data = await res.json();
    localStorage.setItem("token", data.access);
    localStorage.setItem("refresh", data.refresh);
    localStorage.setItem("email", formData.email);
    navigate("/");
    console.log(data);
  };

  return (
    <div className="bg-blue-50 min-h-screen flex items-center justify-center p-5">
      <div className="bg-white shadow-lg rounded-lg p-8 max-w-lg w-full">
        <h1 className="text-4xl text-blue-700 text-center font-bold mb-7">
          Sign In
        </h1>
        <form onSubmit={handleSubmit} className="flex flex-col gap-6">
          <input
            type="email"
            placeholder="Email"
            className="border border-blue-300 p-3 rounded-lg focus:outline-none focus:ring focus:ring-blue-200"
            id="email"
            onChange={handleChange}
          />
          <input
            type="password"
            placeholder="Password"
            className="border border-blue-300 p-3 rounded-lg focus:outline-none focus:ring focus:ring-blue-200"
            id="password"
            onChange={handleChange}
          />
          <button className="bg-blue-700 text-white p-3 rounded-lg uppercase hover:bg-blue-800 disabled:opacity-70">
            Login
          </button>
        </form>
        <div className="flex gap-2 mt-5 text-sm justify-center">
          <p>Don't have an account?</p>
          <Link to={"/signup"}>
            <span className="text-blue-700 hover:underline">Sign up</span>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Login;
