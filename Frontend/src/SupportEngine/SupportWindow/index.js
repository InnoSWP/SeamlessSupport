import React,{useState} from 'react'
import { styles } from '../styles'
import EmailForm from '../SupportWindow/EmailForm'
import ChatEngine from './ChatEngine'
const SupportWindows = props => {
    const[user,setUser]=useState(null)
    const[chat,setChat]=useState(null)
    return (
        <div  className='transition-5'
        style={{...{visibility:props.visible?'visible':'hidden'},...styles.supportWindow
        ,...{opacity:props.visible?'1':'0'}}}>
    
        
            
     
            <EmailForm 
                visible={user === null || chat === null}
                setUser={user => setUser(user)} 
                setChat={chat => setChat(chat)} 
            />

            <ChatEngine 
                visible={user !== null && chat !== null}
                user={user} 
                chat={chat} 
            />
        </div>
    )
}
export default SupportWindows;