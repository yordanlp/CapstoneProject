import { AfterViewInit, Component, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { Observable, Subscription } from 'rxjs';
import { ImageService } from 'src/app/services/image.service';
import { AppConfig } from 'src/app/services/app-config.service';
import { NgForm } from '@angular/forms';
import { Image } from 'src/app/models/image.model';
import { io } from 'socket.io-client';
import { FilterCategories } from 'src/app/models/filter-categories.model';
import { Model } from 'src/app/models/model.model';
import { UserService } from 'src/app/services/user.service';
import { v4 as uuidv4 } from 'uuid';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit, OnDestroy, AfterViewInit {

  imagesObservable$: Observable<any> | null = null;
  imagesSubscription: Subscription | null = null;
  randomImagesSubscription: Subscription | null = null;
  uploadSubscription: Subscription | null = null;
  //socket = io(AppConfig.settings.apiServer.host);
  selectedImage: File | null = null;
  modelDialog: HTMLDialogElement | null = null;
  randomImageDialog: HTMLDialogElement | null = null;
  models: Model[] = [
    {
      description: "Faces",
      name: "faces"
    },
    {
      description: 'Landscapes',
      name: 'alis'
    },
    {
      description: "Cars",
      name: 'cars'
    },
    {
      description: "Cats",
      name: "cats"
    },
    {
      description: "Dogs",
      name: "dogs"
    },
    {
      description: "Wild",
      name: "wild"
    },
    {
      description: "Churches",
      name: "churches"
    }
  ];
  images: Image[] = [];
  allImages: Image[] = [];
  randomImagesNumber: number = 1;
  socket = io(AppConfig.settings.apiServer.host);

  filterCategories: FilterCategories[] = [];

  generateRandomImages( model: string, amount: number){
    console.log(model, amount);
    let eventId = uuidv4();
    let userId = this.userService.getUser().id;
    const key = `${userId}:${eventId}`;
    this.socket.on(key, (data) => {
      this.socket.off(key);
      this.getAllImages();
      console.log(data);
    })
    this.randomImagesSubscription = this.imageService.generateRandomImages(model, amount, this.userService.getUser().id, eventId )
    .subscribe(data => console.log("Generating random", data), error => console.error("Error generando random", error))
    this.randomImagesNumber = 1;
    this.randomImageDialog?.close();
  }

  onFileSelected(event: Event): void {
    let target = event.target as HTMLInputElement;
    this.selectedImage = target?.files![0];
    this.modelDialog?.showModal();
    target.value = '';
  }

  selectModel(model: string): void {
    this.modelDialog?.close();
    if (this.selectedImage != null)
      this.submitImage(this.selectedImage, model);
  }

  submitImage(imageFile: File, model: string) {
    this.uploadSubscription = this.imageService.uploadImage(imageFile, model).subscribe(
      data => console.log(data),
      error => console.error(error)
    );
  }

  getAllImages(){
    this.imagesObservable$ = this.imageService.getImages();
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
      },
      ...this.models.map(m => {
        return {
          name: m.description,
          value: m.name,
          selected: false
        };
      })
    ];

    //this.socket.on('message', (args) => console.log(args));
  }

  onImageDeleted(event: Image) {
    const removeElement = (container :  Image[]) => {
      const index = container.findIndex(image => image.id == event.id);
      if (index !== -1)
        container.splice(index, 1);
    };

    removeElement(this.images);
    removeElement(this.allImages);

    console.log("FILTERING DELETED IMAGE");
  }

  filterBy( category: FilterCategories ){
    const allCat = this.filterCategories.find(category => category.value === '*')!;
      
    if( category.value === '*' ){
      this.filterCategories.forEach(c => c.selected = false);
      category.selected = true;
    }
    else {
      category.selected = !category.selected;
      if (allCat.selected)
        allCat.selected = false;
      else {
        const selectedCategories = this.filterCategories.filter(category => category.selected === true);
        if (selectedCategories.length === 0)
          allCat.selected = true;
      }
    }

    this.images = this.allImages.filter(i => {
      let model = i.model;
      let filter = this.filterCategories.find(f => f.value == model);
      return filter!.selected || allCat.selected;
    });

  }

  ngAfterViewInit(): void {
    this.modelDialog = document.querySelector("#modelPopup") as HTMLDialogElement;
    this.randomImageDialog = document.querySelector("#randomImagePopup") as HTMLDialogElement;
  }
  ngOnDestroy(): void {
    this.imagesSubscription?.unsubscribe();
    this.uploadSubscription?.unsubscribe();
    this.randomImagesSubscription?.unsubscribe();
    this.socket.close();
  }
  ngOnInit(): void {
    this.getAllImages();
  }

  showRandomImagePopup(){
    this.randomImageDialog?.showModal();
  }
}
