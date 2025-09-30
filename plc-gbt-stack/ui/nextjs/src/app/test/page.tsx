'use client';

export default function TestPage() {
  return (
    <div className="h-screen w-screen flex items-center justify-center bg-[#1e1e1e]">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-white mb-4">React Test Page</h1>
        <p className="text-xl text-gray-300">If you can see this, React is working!</p>
        <button
          onClick={() => alert('Button clicked!')}
          className="mt-4 px-6 py-3 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Click Me
        </button>
      </div>
    </div>
  );
}

