import { outputAst } from '@angular/compiler';
import { Component, EventEmitter, Input, OnDestroy, OnInit, Output } from '@angular/core';
import { Observable, Subscription } from 'rxjs';
import { SavedImage } from 'src/app/models/saved-image.model';
import { Image } from 'src/app/models/image.model';
import { ImageService } from 'src/app/services/image.service';

@Component({
  selector: 'app-saved-image-card',
  templateUrl: './saved-image-card.component.html',
  styleUrls: ['./saved-image-card.component.css']
})
export class SavedImageCardComponent implements OnInit, OnDestroy {
  @Input() imageData: SavedImage = null!;
  @Output() imageDeleted: EventEmitter<SavedImage> = new EventEmitter<SavedImage> ();
  imageBlob$: Observable<any> = null!
  imageSubscription: Subscription = null!;
  blobUrl: string = ""
  isImageLoaded = false;

  constructor(private imageService: ImageService) {

  }

  onImageLoad(){
    this.isImageLoaded = true;
  }
  
  deleteImage(): void {
    console.log('REMOVING IMAGE');
    console.log(this.imageData);
    this.imageSubscription = this.imageService.deleteSavedImage(this.imageData.id).subscribe((response) => {
      console.log(response);
      this.imageDeleted.emit(this.imageData);
      console.log("EVENT EMITTED");
    }, (error) => {
      console.log(error);
    });
  }

  ngOnDestroy(): void {
    this.imageSubscription?.unsubscribe();
  }
  ngOnInit(): void {
    this.imageBlob$ = this.imageService.getSavedImage(this.imageData.id);
    this.imageSubscription = this.imageBlob$.subscribe(data => {
      this.blobUrl = URL.createObjectURL(data);
      console.log(this.blobUrl);
    });
  }
}
