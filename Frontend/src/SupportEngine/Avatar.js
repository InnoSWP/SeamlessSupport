import { useState,React} from "react"
import { styles, Styles } from './styles'
const Avatar = props=>{
    const[Hover,setHover]=useState(false)
   

    return(
        <div style={props.style}  >
            <div className='transition-3'
            style={{...styles.avatarHello,...{opacity:Hover?1:0},...{display:Hover?'inline':'none'}}}
            
            >Hey I'm support chat</div>
            <div className='transition-3'  
            onMouseLeave={()=>setHover(false)}
            onMouseEnter={()=>setHover(true)}
         
            onClick={()=>props.onClick&&props.onClick()}
            style={{
                ...styles.chatWithMeButton,
                ...{border:Hover?'3px solid #6195ff':'1px solid #f9f0ff '}
            }}
            
            />
            
        </div>
    )
}
export default Avatar;