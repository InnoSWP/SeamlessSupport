import React,{useState,useRef,useEffect} from 'react'
import Avatar from './Avatar'
import SupportWindows from './SupportWindow'
const SupportEngine = () => {
    const ref=useRef(null)
    const[visible,setVisible]=useState(false)
    useEffect(()=>{
        function handleClickOutside(event) {
            if (ref.current && !ref.current.contains(event.target)) {
                setVisible(false)
            }
        }
        document.addEventListener("mousedown", handleClickOutside);
        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    },[ref])
    return (
        <div ref={ref}> 
            <SupportWindows visible={visible}/>
            <Avatar onClick={()=>{setVisible(true)}} style={{bottom:'24px',right:'40px',position:'absolute'}}/>
        </div>
      );
}
 
export default SupportEngine;