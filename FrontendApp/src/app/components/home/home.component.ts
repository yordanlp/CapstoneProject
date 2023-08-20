import { AfterViewInit, Component, ElementRef, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { Observable, Subscription } from 'rxjs';
import { ImageService } from 'src/app/services/image.service';
import { AppConfig } from 'src/app/services/app-config.service';
import { NgForm } from '@angular/forms';
import { Image } from 'src/app/models/image.model';
import { FilterCategories } from 'src/app/models/filter-categories.model';
import { Model } from 'src/app/models/model.model';
import { UserService } from 'src/app/services/user.service';
import { v4 as uuidv4 } from 'uuid';
import { WebSocketService } from 'src/app/services/web-socket.service';
import { ToastrService } from 'ngx-toastr';

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
  selectedImage: File | null = null;
  @ViewChild('modelDialog', { static: false }) modelDialog!: ElementRef<HTMLDialogElement>;
  @ViewChild('randomImageDialog', { static: false }) randomImageDialog!: ElementRef<HTMLDialogElement>;
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

  filterCategories: FilterCategories[] = [];

  generateRandomImages( model: string, amount: number){
    let eventId = uuidv4();
    let userId = this.userService.getUser().id;
    const key = `${userId}:${eventId}`;
    this.ws.on(key, (data: string) => {
      this.ws.off(key);
      this.getAllImages();
      let dataParsed = JSON.parse(data);
      if( dataParsed.success )
        this.toastr.success("Images generated successfully");
      else
        this.toastr.error("An error has ocurred generating the images");
    });
    this.randomImagesSubscription = this.imageService.generateRandomImages(model, amount, this.userService.getUser().id, eventId )
    .subscribe(data => console.log("Generating random", data), error => console.error("Error generando random", error))
    this.randomImagesNumber = 1;
    this.randomImageDialog.nativeElement.close();
  }

  onFileSelected(event: Event): void {
    let target = event.target as HTMLInputElement;
    this.selectedImage = target?.files![0];
    this.modelDialog.nativeElement.showModal();
    target.value = '';
  }

  selectModel(model: string): void {
    this.modelDialog.nativeElement.close();
    if (this.selectedImage != null)
      this.submitImage(this.selectedImage, model);
  }

  submitImage(imageFile: File, model: string) {
    this.uploadSubscription = this.imageService.uploadImage(imageFile, model).subscribe(
      data => {
        if( !data.success )
          console.error(data);
        let image = {
          id : data.data.id,
          mime_type : data.data.mime_type,
          model : data.data.model,
          name : data.data.name,
          user_id : data.data.user_id,
          status_process: null
        } as Image;
        this.allImages = [image, ...this.allImages];
        this.applyFilter();
        const imageId = data.data.id;
        let eventId = uuidv4();
        let userId = this.userService.getUser().id;
        this.imageService.generateProjection(imageId, userId, eventId).subscribe(
          data => {
            if( !data.success )
              console.error(data);
            const key = `${userId}:${eventId}`;
            this.ws.on(key, (data: string) => {
              this.ws.off(key);
              let dataParsed = JSON.parse(data);
              if( !dataParsed.success ){
                console.error(dataParsed.message);
                return;
              }
              let idx = this.allImages.findIndex(i => i.id == image.id);
              if( idx >= 0 ){
                let newImg = {...this.allImages[idx]};
                newImg.status_process = 'FINISH';
                this.allImages.splice(idx, 1, newImg);
              }
              this.applyFilter();
              this.toastr.success("Image Projection has finished successfully", "Projection Finished");
            });
          },
          error => console.error(error)
        );
      },
      error => console.error(error)
      );
    
  }
  getAllImages(){
    this.imagesObservable$ = this.imageService.getImages();
    this.imagesSubscription = this.imagesObservable$?.subscribe(
      data => {
        this.images = data.data;
        this.allImages = [...this.images];
      }
      , error => console.error(error)
    ) ?? null;
  }

  constructor(private imageService: ImageService
    , private userService: UserService
    , private ws: WebSocketService
    , private toastr: ToastrService) {
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
  }

  onImageDeleted(event: Image) {
    const removeElement = (container :  Image[]) => {
      const index = container.findIndex(image => image.id == event.id);
      if (index !== -1)
        container.splice(index, 1);
    };

    removeElement(this.images);
    removeElement(this.allImages);
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

    this.applyFilter();

  }

  applyFilter(){
    const allCat = this.filterCategories.find(category => category.value === '*')!;

    this.images = this.allImages.filter(i => {
      let model = i.model;
      let filter = this.filterCategories.find(f => f.value == model);
      return filter!.selected || allCat.selected;
    });
  }

  ngAfterViewInit(): void {
  }
  ngOnDestroy(): void {
    this.imagesSubscription?.unsubscribe();
    this.uploadSubscription?.unsubscribe();
    this.randomImagesSubscription?.unsubscribe();
  }
  ngOnInit(): void {
    this.getAllImages();
  }

  showRandomImagePopup(){
    this.randomImageDialog.nativeElement.showModal();
  }
}
