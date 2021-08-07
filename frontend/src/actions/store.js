import {
  configureStore,
  getDefaultMiddleware
} from "@reduxjs/toolkit";
import createSagaMiddleware from "redux-saga";
import sagas from "./sagas"
import reducers from './reducers'
import { routerMiddleware } from 'connected-react-router'
import { createBrowserHistory } from 'history'
import { connectRouter } from 'connected-react-router'
import { combineReducers } from 'redux'

export const history = createBrowserHistory()

let sagaMiddleware = createSagaMiddleware();
const middleware = [...getDefaultMiddleware({ thunk: false, serializableCheck: { ignoredActions: ['UPLOADING_FILE']} }), sagaMiddleware, routerMiddleware(history)];

const createRootReducer = combineReducers({
  router: connectRouter(history),
  ...reducers
})

const store = configureStore({
  reducer: createRootReducer,
  middleware
});

sagaMiddleware.run(sagas);

export default store;
