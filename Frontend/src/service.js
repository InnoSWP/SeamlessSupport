
import { faCoffee } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { dom } from '@fortawesome/fontawesome-svg-core'


const Service = () => {
    return ( 
       
        <div class="over pd-y">
         <div class="section-header" id="serviceid">
             <h2 class="section-tiltle">What we offer</h2>
             <span class="line"></span>
          </div>
            <div class="container pd-y"> 
          <div class="offer-content">
             <div class="offer-item ltr-effect">
             <i class="icon fa fa-diamond fa-2x"></i>
                 <h2 class="offer-item-title">App development</h2>
                
             </div>
             <div class="offer-item mg ltr-effect">
                
                 <i class="icon fa fa-rocket fa-2x"></i>
                 <h2 class="offer-item-title">graphic desgin</h2>
             
             </div>
             <div class="offer-item ltr-effect">
                 <i class="icon fa fa-cogs fa-2x"></i>
                 <h2 class="offer-item-title">creative idea</h2>
                
             </div>
             <div class="offer-item ltr-effect">
                 <i class="icon fa fa-diamond fa-2x"></i>
                 <h2 class="offer-item-title">marketing</h2>
               
             </div>
             <div class="offer-item mg ltr-effect">
                 <i class="icon fa fa-pencil fa-2x"></i>
                 <h2 class="offer-item-title">awesome support</h2>
                 
             </div>
             <div class="offer-item ltr-effect">
                 <i class="icon fa fa-flask fa-2x"></i>
                 <h2 class="offer-item-title">brand design</h2>
                 
             </div>
 
             <div class="clear"></div>
          </div>
            </div>
        </div>
     );
}
 
export default Service;