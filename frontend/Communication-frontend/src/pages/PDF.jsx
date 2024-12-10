import React from "react";
import jsPDF from "jspdf";

const PDF = () => {
  const generatePDF = () => {
    const doc = new jsPDF();

    // Add a title
    doc.setFontSize(18);
    doc.text("Sample PDF Report", 20, 20);

    // Add some content
    doc.setFontSize(12);
    doc.text("This is a simple PDF report generated using jsPDF.", 20, 40);
    doc.text("You can customize this content as needed.", 20, 50);

    // Add a table or dynamic data (example)
    const data = [
      { Name: "John Doe", Age: 28, Department: "Engineering" },
      { Name: "Jane Smith", Age: 34, Department: "Marketing" },
    ];
    let y = 70;
    doc.text("Name\t\tAge\t\tDepartment", 20, y); // Header
    y += 10;
    data.forEach((item) => {
      doc.text(`${item.Name}\t\t${item.Age}\t\t${item.Department}`, 20, y);
      y += 10;
    });

    // Save the document
    doc.save("report.pdf");
  };

  return (
    <div className="bg-gray-100 min-h-screen flex flex-col items-center justify-center">
      <h1 className="text-2xl font-bold mb-4">Generate PDF Report</h1>
      <button
        onClick={generatePDF}
        className="bg-blue-600 text-white px-6 py-3 rounded-lg shadow-lg hover:bg-blue-700"
      >
        Download PDF
      </button>
    </div>
  );
};

export default PDF;
