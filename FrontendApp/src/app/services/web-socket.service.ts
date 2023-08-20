import { Injectable } from '@angular/core';
import { Socket, io } from 'socket.io-client';
import { AppConfig } from './app-config.service';

@Injectable({
  providedIn: 'root'
})
export class WebSocketService {

  private socket: Socket = null!;
  constructor() {
    this.socket = io(AppConfig.settings.apiServer.host)
   }

   on(key: string, callback: any): void{
    if( typeof(callback) != 'function' )
      throw { 'message': 'Invalid argument (callback)' };
    this.socket.on(key, callback);
   }

   off(key: string): void{
    this.socket.off(key);
   }

}
