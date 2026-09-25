import { Routes, Route } from 'react-router-dom'
import Header from './components/Header.jsx'
import Sidebar from './components/Sidebar.jsx'
import Dashboard from './pages/Dashboard.jsx'
import IndividualSelect from './pages/IndividualSelect.jsx'
import IndividualUpload from './pages/IndividualUpload.jsx'
import IndividualProcessing from './pages/IndividualProcessing.jsx'
import IndividualResult from './pages/IndividualResult.jsx'
import MultiNewCase from './pages/MultiNewCase.jsx'
import MultiProcessing from './pages/MultiProcessing.jsx'
import MultiResult from './pages/MultiResult.jsx'
import History from './pages/History.jsx'
import SystemStatus from './pages/SystemStatus.jsx'

export default function App() {
  return (
    <div className="min-h-screen bg-bg">
      <Header />
      <div className="flex">
        <Sidebar />
        <main className="min-w-0 flex-1">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/individual" element={<IndividualSelect />} />
            <Route path="/individual/:moduleId/upload" element={<IndividualUpload />} />
            <Route path="/individual/:moduleId/processing" element={<IndividualProcessing />} />
            <Route path="/individual/:moduleId/result" element={<IndividualResult />} />
            <Route path="/multi" element={<MultiNewCase />} />
            <Route path="/multi/processing" element={<MultiProcessing />} />
            <Route path="/multi/result" element={<MultiResult />} />
            <Route path="/history" element={<History />} />
            <Route path="/system-status" element={<SystemStatus />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}
