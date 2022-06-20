import React,{useState} from 'react'
import { styles } from '../styles'
import EmailForm from '../SupportWindow/EmailForm'
import ChatEngine from './ChatEngine'
import io from "socket.io-client";
const SupportWindows = props => {
    const[Show,setShow]=useState(true)
    const [email,setEmail]=useState("")
    const socket = io.connect ("");
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
