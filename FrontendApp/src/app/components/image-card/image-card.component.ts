import { Component, EventEmitter, Input, OnDestroy, OnInit, Output } from '@angular/core';
import { Observable, Subscription } from 'rxjs';
import { Image } from 'src/app/models/image.model';
import { ImageService } from 'src/app/services/image.service';

@Component({
  selector: 'app-image-card',
  templateUrl: './image-card.component.html',
  styleUrls: ['./image-card.component.css']
})
export class ImageCardComponent implements OnInit, OnDestroy {

  private _imageData: Image = null!;
  @Input() set imageData( value: Image ){
    this._imageData = value;
    console.log("ImageData", value);
  }

  get imageData(){
    return this._imageData;
  }
  
  @Output() imageDeleted: EventEmitter<Image> = new EventEmitter<Image> ();
  imageBlob$: Observable<any> = null!
  imageSubscription: Subscription = null!;
  blobUrl: string = "";
  isImageLoaded = false;

  constructor(private imageService: ImageService) {

  }

  deleteImage(): void {
    console.log('REMOVING IMAGE');
    console.log(this.imageData);
    this.imageSubscription = this.imageService.deleteImage(this.imageData.id).subscribe((response) => {
      console.log(response);
      this.imageDeleted.emit(this.imageData);
    }, (error) => {
      console.log(error);
    });
  }

  onImageLoad(){
    this.isImageLoaded = true;
    console.log("Image Loaded");
  }

  ngOnDestroy(): void {
    this.imageSubscription?.unsubscribe();
  }
  ngOnInit(): void {
    this.imageBlob$ = this.imageService.getImage(this.imageData.id);
    this.imageSubscription = this.imageBlob$.subscribe(data => {
      this.blobUrl = URL.createObjectURL(data);
      console.log(this.blobUrl);
    });
  }
}
