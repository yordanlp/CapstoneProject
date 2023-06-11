import { Component, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { Observable, Subscription } from 'rxjs';
import { ImageService } from 'src/app/services/image.service';
import { AppConfig } from 'src/app/services/app-config.service';
import { NgForm } from '@angular/forms';
import { Image } from 'src/app/models/image.model';
import { io } from 'socket.io-client';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit, OnDestroy {

  imagesObservable$: Observable<any> | null = null;
  imagesSubscription: Subscription | null = null;
  uploadSubscription: Subscription | null = null;
  socket = io(AppConfig.settings.apiServer.host);

  onFileSelected(event: Event): void {
    let target = event.target as HTMLInputElement;
    this.submitImage(target?.files![0])
  }

  submitImage(imageFile: File) {
    const formData = new FormData();
    formData.append('image', imageFile, imageFile.name);
    this.uploadSubscription = this.imageService.uploadImage(imageFile).subscribe(
      data => console.log(data),
      error => console.error(error)
    );
  }

  constructor(private imageService: ImageService) {
    this.imagesObservable$ = this.imageService.getImages();
    this.socket.on('message', (args) => console.log(args));

  }
  ngOnDestroy(): void {
    this.imagesSubscription?.unsubscribe();
    this.uploadSubscription?.unsubscribe();
    this.socket.close();
  }
  ngOnInit(): void {
    this.imagesSubscription = this.imagesObservable$?.subscribe(
      data => console.log(data)
      , error => console.error(error)
    ) ?? null;
  }



}
