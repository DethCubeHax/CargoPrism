import Navbar from "./components/Navbar";
import Pages from "./pages/Pages";
import { BrowserRouter } from "react-router-dom";

function App() {
  return (
    <div className="App" style={{fontFamily: "DM Sans"}}>
      <BrowserRouter>
        <Navbar />
        <Pages />
      </BrowserRouter>
    </div>
  );
}

export default App;
