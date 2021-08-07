import { all } from 'redux-saga/effects';
import authSaga from 'containers/sessions/redux/saga'
import fileSaga from 'containers/files/redux/saga'
import accountSaga from 'containers/accounts/redux/saga'

export default function* rootSaga(getState) {
  yield all([
    authSaga(),
    accountSaga(),
    fileSaga()
  ]);
}
