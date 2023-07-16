import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { AppConfig } from './app-config.service';
import { BehaviorSubject, Observable } from 'rxjs';
import { User } from '../models/user.model';

@Injectable({
  providedIn: 'root'
})
export class UserService {

  private _isLoggedIn$ = new BehaviorSubject<boolean>(false);
  private _user$ = new BehaviorSubject<User | null>(null);
  isLoggedIn$ = this._isLoggedIn$.asObservable();
  user = this._user$.asObservable();

  constructor(private http: HttpClient) {
    if (localStorage.getItem('user-token') == null)
      this.setLogInStatus(false, null, '');
    else {
      const user = JSON.parse(localStorage.getItem('user')!) as User;
      const token = localStorage.getItem('user-token')!;
      this.setLogInStatus(true, user, token);
    }
  }

  registerUser(username: string, email: string, password: string) {
    const body = {
      username: username,
      email: email,
      password: password
    };
    return this.http.post(`${AppConfig.settings.apiServer.host}/api/users/register`, body);
  }

  login(email: string, password: string): Observable<any> {
    return this.http.post(`${AppConfig.settings.apiServer.host}/api/users/login`, { email, password });
  }

  setLogInStatus(status: boolean, user: User | null, token: string): void {
    if (status) {
      localStorage.setItem('user', JSON.stringify(user));
      localStorage.setItem('user-token', token);
    } else {
      localStorage.removeItem('user');
      localStorage.removeItem('user-token');
    }
    this._isLoggedIn$.next(status);
    this._user$.next(user);
  }

  logout(): void {
    this.setLogInStatus(false, null, '');
    localStorage.removeItem('user-token');
  }

  getUser(): User{
    const user = JSON.parse(localStorage.getItem('user')!) as User;
    return user;
  }
}

