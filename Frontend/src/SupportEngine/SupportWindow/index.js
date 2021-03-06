import React,{useState} from 'react'
import { styles } from '../styles'
import EmailForm from '../SupportWindow/EmailForm'
import ChatEngine from './ChatEngine'
const SupportWindows = props => {
    const[Show,setShow]=useState(true)
    const [email,setEmail]=useState("")
   
          const socket = require("socket.io-client")("http://127.0.0.1:5000/");
      
    return (
        <div  className='transition-5'
        style={{...{visibility:props.visible?'visible':'hidden'},...styles.supportWindow
        ,...{opacity:props.visible?'1':'0'}}}>
    

            <EmailForm 
               visible={Show===true}
               setShow={show => setShow(show)} 
                setEmail={email => setEmail(email)}
           
            />
            
                  
    <ChatEngine 
               visible={Show===false}
              email={email}
              socket={socket}
            />
     
         
        </div>
    )
}
export default SupportWindows;
