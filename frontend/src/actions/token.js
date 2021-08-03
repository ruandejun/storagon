export class Token {
    static setUser(user) {
      localStorage.setItem('tokenUser', JSON.stringify(user));
    }
  
    static getUser() {
      const data = localStorage.getItem('tokenUser');
  
      return data ? JSON.parse(data) : null;
    }
  
    static setToken(token) {
      localStorage.setItem('dt_token', token);
    }
  
    static getToken() {
      return localStorage.getItem('dt_token');
    }
  
    static destroy() {
      localStorage.removeItem('tokenUser');
      localStorage.removeItem('dt_token');
    }
  }
  
  export default Token
  