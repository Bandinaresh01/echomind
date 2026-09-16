import { Routes, Route } from 'react-router-dom';
import ChatPage from '@/pages/ChatPage';
import LandingPage from '@/components/LandingPage';
import DocsPage from '@/pages/DocsPage';
import TeamPage from '@/pages/TeamPage';
import Layout from '@/components/Layout';

function App() {
  return (
    <Routes>
      <Route path="/" element={<ChatPage />} />
      <Route path="/chat" element={<ChatPage />} />
      <Route element={<Layout />}>
        <Route path="/landing" element={<LandingPage />} />
        <Route path="/docs" element={<DocsPage />} />
        <Route path="/team" element={<TeamPage />} />
      </Route>
    </Routes>
  );
}

export default App;
