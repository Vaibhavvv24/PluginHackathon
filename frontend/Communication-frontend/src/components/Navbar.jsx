import React from "react";
import { Link } from "react-router-dom";

const Navbar = () => {
  return (
    <nav className="bg-blue-500 text-white shadow-lg">
      <div className="container mx-auto flex justify-between items-center p-4">
        <h1 className="text-2xl font-bold">
          <Link to="/">AI Communication System</Link>
        </h1>
        <ul className="flex space-x-6">
          <li>
            <Link
              to="/take-assessment"
              className="hover:bg-blue-700 px-4 py-2 rounded"
            >
              Take Assessment
            </Link>
          </li>
          <li>
            <Link to="/login" className="hover:bg-blue-700 px-4 py-2 rounded">
              Login
            </Link>
          </li>
          <li>
            <Link to="/profile" className="hover:bg-blue-700 px-4 py-2 rounded">
              Profile
            </Link>
          </li>
          <li>
            <Link to="/history" className="hover:bg-blue-700 px-4 py-2 rounded">
              User History
            </Link>
          </li>
        </ul>
      </div>
    </nav>
  );
};

export default Navbar;
