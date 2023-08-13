import { Component } from '@angular/core';
import { Observable, Subscription } from 'rxjs';
import { io } from 'socket.io-client';
import { FilterCategories } from 'src/app/models/filter-categories.model';
import { Image } from 'src/app/models/image.model';
import { SavedImage } from 'src/app/models/saved-image.model';
import { AppConfig } from 'src/app/services/app-config.service';
import { ImageService } from 'src/app/services/image.service';
import { UserService } from 'src/app/services/user.service';

@Component({
  selector: 'app-saved-images',
  templateUrl: './saved-images.component.html',
  styleUrls: ['./saved-images.component.css']
})
export class SavedImagesComponent {
  imagesObservable$: Observable<any> | null = null;
  imagesSubscription: Subscription | null = null;
  //socket = io(AppConfig.settings.apiServer.host);
  selectedImage: File | null = null;
  modelDialog: HTMLDialogElement | null = null;
  randomImageDialog: HTMLDialogElement | null = null;
  images: SavedImage[] = [];
  allImages: SavedImage[] = [];
  randomImagesNumber: number = 1;
  socket = io(AppConfig.settings.apiServer.host);

  filterCategories: FilterCategories[] = []

  getAllImages(){
    this.imagesObservable$ = this.imageService.getSavedImages();
    this.imagesSubscription = this.imagesObservable$?.subscribe(
      data => {
        console.log(data)
        this.images = data.data;
        this.allImages = [...this.images];
        console.log(this.images);
      }
      , error => console.error(error)
    ) ?? null;
  }

  constructor(private imageService: ImageService, private userService: UserService) {
    this.filterCategories = [
      {
        name: 'All categories',
        value: '*',
        selected: true
      }
    ];

    //this.socket.on('message', (args) => console.log(args));
  }

  ngOnDestroy(): void {
    this.imagesSubscription?.unsubscribe();
    this.socket.close();
  }
  ngOnInit(): void {
    this.getAllImages();
  }
}
