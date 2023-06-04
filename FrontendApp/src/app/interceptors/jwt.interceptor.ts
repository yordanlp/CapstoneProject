import { Injectable } from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor
} from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable()
export class JwtInterceptor implements HttpInterceptor {
  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // get the token from local storage
    let jwtToken = localStorage.getItem('user-token');

    if (jwtToken) {
      // clone the request and replace the original headers with
      // cloned headers, updated with the authorization.
      const authReq = request.clone({
        headers: request.headers.set('Authorization', `Bearer ${jwtToken}`)
      });

      // send the newly created request
      return next.handle(authReq);
    } else {
      return next.handle(request);
    }
  }
}
