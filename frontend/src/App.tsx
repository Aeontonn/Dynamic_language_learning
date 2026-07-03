import { Route, Routes } from "react-router-dom";
import { Dashboard } from "./pages/Dashboard";
import { Review } from "./pages/Review";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/review" element={<Review />} />
    </Routes>
  );
}

export default App;
