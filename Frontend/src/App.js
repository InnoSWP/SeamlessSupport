

import Home from "./home";
import {BrowserRouter as Router, Route, Switch} from 'react-router-dom';
import Navbar from './navbar';
import Service from "./service";
import Contact from "./contact";
import Frequentqu from "./frequentqu";
import SupportEngine from "./SupportEngine";

function App() {
  return (

     
    <Router> 
      <Navbar/>
    
     <Home/>
 
     <Service/>
     <Frequentqu/>
    <Contact/>
    <SupportEngine/>
    </Router>
        
        
          
  );
}

export default App;

