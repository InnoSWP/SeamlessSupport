import React, { useState } from "react"

import { styles } from "../styles"

import Avatar from '../Avatar'

const EmailForm = props => {    
    const [email, setEmail] = useState('')
 

    function handleSubmit(event) {
        const regEx = /[a-zA-Z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,8}(.[a-z{2,8}])?/g;
        if (regEx.test(email)) {
            event.preventDefault();
      props.setShow(false)
            props.setEmail(email)
        } else if (!regEx.test(email) && email !== "") {
         window.alert("Email is Not Valid");
        } else {
            window.alert("Please Enter Email");
        }
     
    }

    return (
        <div 
            style={{
                ...styles.emailFormWindow,
                ...{ 
                    height: props.visible ? '100%' : '0px',
                    opacity: props.visible ? '1' : '0',
                    visibility: props.visible ? 'visible' :'hidden'
                  
                    
                }
            }}
        >
            <div style={{ height: '0px' }}>
                <div style={styles.stripe} />
            </div>

        
    
            <div style={{ position: 'absolute', height: '100%', width: '100%', textAlign: 'center' }}>
      
                <Avatar 
                    style={{ 
                        position: 'relative',
                        left: 'calc(50% - 44px)',
                        top: '10%',
                        visibility: props.visible ? 'visible' :'hidden'
                    }}
                />

                <div style={styles.topText}>
                    Welcome to my <br /> support 👋 
                 
                </div>

                <form 
                    onSubmit={e =>handleSubmit(e)}
                    style={{ visibility: props.visible ? 'visible' :'hidden', position: 'relative', width: '100%', top: '19.75%' }}
                    method="POST"
                >
                    <input 
                        placeholder='Your Email'
                    type={'email'}
                    id="email"
                    name="email"
                    className="input"
                    value={email}
                        onChange={e => setEmail(e.target.value)}
                        style={styles.emailInput}
                    />
                </form>
                
                <div style={styles.bottomText}>
                    Enter your email 
                    <br />
                    to get started

                </div>
            </div>
        </div>
    )
}

export default EmailForm;
