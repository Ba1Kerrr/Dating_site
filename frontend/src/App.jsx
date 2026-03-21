import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { useEffect } from 'react'
import { PrivateRoute } from './components'
import useAuthStore from './store/useAuthStore'

import Home from './pages/Home'
import About from './pages/About'
import ChatList from './pages/ChatList'
import ChatRoom from './pages/ChatRoom'
import Profile from './pages/Profile'
import DopInfo from './pages/DopInfo'
import PrivacyPolicy from './pages/Policy'
import Terms from './pages/Terms'
import SubscriptionPage from './pages/SubscriptionPage'

function App() {
  const { fetchMe } = useAuthStore()

  useEffect(() => { fetchMe() }, [])

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/"                    element={<Home />} />
        <Route path="/about"               element={<About />} />
        <Route path="/privacy"             element={<PrivacyPolicy />} />
        <Route path="/terms"               element={<Terms />} />

        <Route path="/subscription"      element={<PrivateRoute><SubscriptionPage /></PrivateRoute>} />
        <Route path="/register/dop-info"   element={<PrivateRoute><DopInfo /></PrivateRoute>} />
        <Route path="/chat"                element={<PrivateRoute><ChatList /></PrivateRoute>} />
        <Route path="/chat/:companion"     element={<PrivateRoute><ChatRoom /></PrivateRoute>} />
        <Route path="/users/:username"     element={<PrivateRoute><Profile /></PrivateRoute>} />
        <Route path="/profile/:username"   element={<PrivateRoute><Profile /></PrivateRoute>} />
      </Routes>
    </BrowserRouter>
  )
}

export default App