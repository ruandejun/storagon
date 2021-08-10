import React from 'react'
import ReactDOM from 'react-dom'
import './index.css'
import App from './App'
import store from './actions/store'
import { Provider } from 'react-redux'
import fontawesome from '@fortawesome/fontawesome'
import { faTrash, faPaste, faEdit, faWallet, faCut, faFolderPlus, faLevelUpAlt, faCheckDouble, faMinusSquare, 
        faRetweet, faCheck, faSync, faPencilAlt, faFileUpload, faSearch, faInfo, faTimes,
      faFileDownload, faTh, faBars, faSort, faCog, faFolder, faFolderOpen, faChevronRight, faChevronDown } from '@fortawesome/free-solid-svg-icons'

fontawesome.library.add(faTimes, faChevronRight, faChevronDown, faFolder, faFolderOpen, faSort, faPaste, faWallet, faCog, faTrash, faCut, faEdit, faFolderPlus, faLevelUpAlt, faCheckDouble, faMinusSquare,  faRetweet, faCheck, faSync, faPencilAlt, faFileUpload, faSearch, faInfo, faFileDownload, faTh, faBars)
ReactDOM.render(
  <React.StrictMode>
    <Provider store={store}>
      <App />
    </Provider>
  </React.StrictMode>,
  document.getElementById('root')
)