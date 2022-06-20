import React, { useEffect, useState ,useRef} from "react";
import Avatar from "../Avatar";
const ChatEngine = ({visible,email,socket}) => {
  
   const[messages,setMessages]=useState("")
    const[message,setMessage]=useState([])
    const messageRef = useRef();
    
    useEffect(() => {
        if (messageRef.current) {
          messageRef.current.scrollIntoView(
            {
              behavior: 'smooth',
              block: 'end',
              inline: 'nearest'
            })
        }
      })
 
   socket.on('connect', function() {
    socket.emit('join', {});
}); 
   const sendMessage= async  ()=> {
    if(messages!==""){
     await   socket.emit('text', {msg: messages});
     setMessage((list)=>[...list,messages])
        setMessages("")
  
    }

   

    }
    useEffect(() => {
        socket.on('message', (data) => {
         setMessage((list)=>[...list,data.msg])

        },
  
        )
    

    }, [socket]);


  
    return (
        
        <div
            className='transition-5'
            style={{
                ...styles.chatEngineWindow,
                ...{ 
                    height: visible ? '100%' : '0px',
                    zIndex: visible ? '100' : '0px',
                    visibility: visible ? 'visible' : 'hidden',
                  
                }
            }}

        >   
            <div className="chat-body" style={{...styles.chatbody,...styles.Scroll,...{  visibility: visible ? 'visible' :'hidden'}} } >
          
        <div style={{...styles.chatwindow}} >
    
            {message.map((item,index)=>{
                return(
                <div style={{...styles.messager}} ref={messageRef}>
                    
                    <div style={{...styles.content}} >
                    <p>{item}</p>
                  </div>
                 </div>
                )

            }

            )}
               
            </div>
           
            </div>
            <input style={{...styles.text}}  onKeyPress={(event) => {
            event.key === "Enter" && sendMessage();
          }}  onChange={(e)=>setMessages(e.target.value)}  id="text" size="60" placeholder="   Enter your message here"  value={messages}  />
      <button style={{...styles.button}} onClick={sendMessage} >Send</button><br /><br />
           <br /><br />
  
      
            
        </div>
    )
}

export default ChatEngine;

const styles = {
    chatEngineWindow: {
        width: '100%',  
        backgroundColor: '#fff',
    },
    chatwindow:{
        position: 'absolute',
        top:'1%',
        bottom: '51%',
        left:' 0',
      right: '0',
      margin: '0',
      width:'100% ',
      height:'92%',
      padding: '30px ',
    },
    text:{
        position: 'absolute',
        top: '94%',
        left:'1%',
        width: '80%',
        height:'5%',
    
        border:'4px'
    }
    ,
    button:{
        position: 'absolute',
        top: '94%',
        width: '20%',
        height:'5%',
        left:'81%',
        cursor: 'pointer',
        fontSize: '18px',
        border:'4px',
        color: 'black',
        backgroundColor:'#e8e8e8',
        letterSpacing: '2px',
        lineHeight: '1.5px'

    }
    ,
    Scroll:{
        
      
        overflowY: "scroll",
        overflowX: "hidden"
        


    }
    ,
    content:{
        width: "auto",
        height: "auto",
        minHeight:" 50px",
    
        backgroundColor: "#6195ff",
        borderRadius: "5px",
        color:" white",
        display: "flex",
        alignItems: "center",
        marginRight: "5px",
        marginLeft: '5px',
        paddingRight: "5px",
        paddingLeft:" 5px",
        overflowWrap: "break-word",
        wordBreak: "break-word",
    },
    chatbody:
    {
        height: "93%",
        border:" 1px solid #263238",
        background:" #fff",
      
        position: "relative"
    },
    messager:{
        height: "auto",
  padding: "10px",
  display: "flex"
    }
}
