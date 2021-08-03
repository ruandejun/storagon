import { all } from 'redux-saga/effects';
import authSaga from 'containers/sessions/redux/saga'

export default function* rootSaga(getState) {
  yield all([
    authSaga()
  ]);
}
