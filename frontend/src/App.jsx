import { useEffect, useState } from 'react';
import Login from './components/Login';
import Dashboard from './components/Dashboard';

function App() {
  const [loggedIn, setLoggedIn] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const requestToken = params.get('request_token');
    const error = params.get('error');

    if (requestToken) {
      // You might want to do something with the token here,
      // like sending it to your backend to finalize the session,
      // but for now, we'll just consider the user logged in.
      setLoggedIn(true);
    }

    if (error) {
      alert(`An error occurred: ${error}`);
    }
  }, []);

  return <div className="App">{loggedIn ? <Dashboard /> : <Login />}</div>;
}

export default App;
