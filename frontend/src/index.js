import React from 'react'
import ReactDOM from 'react-dom'
import './index.css'
import App from './App'
import store from './actions/store'
import { Provider } from 'react-redux'
import { setChonkyDefaults } from 'chonky';
import { ChonkyIconFA } from 'chonky-icon-fontawesome'

setChonkyDefaults({ iconComponent: ChonkyIconFA })
ReactDOM.render(
  <React.StrictMode>
    <Provider store={store}>
      <App />
    </Provider>
  </React.StrictMode>,
  document.getElementById('root')
)