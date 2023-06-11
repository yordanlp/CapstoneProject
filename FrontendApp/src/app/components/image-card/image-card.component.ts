import { Component, Input, OnInit } from '@angular/core';
import { Observable, Subscription } from 'rxjs';
import { Image } from 'src/app/models/image.model';
import { ImageService } from 'src/app/services/image.service';

@Component({
  selector: 'app-image-card',
  templateUrl: './image-card.component.html',
  styleUrls: ['./image-card.component.css']
})
export class ImageCardComponent implements OnInit {

  @Input() imageData: Image = null!;
  imageBlob$: Observable<any> = null!
  imageSubscription: Subscription = null!;
  blobUrl: string = ""

  constructor(private imageService: ImageService) {

  }
  ngOnInit(): void {
    this.imageBlob$ = this.imageService.getImage(this.imageData.id);
    this.imageSubscription = this.imageBlob$.subscribe(data => {
      this.blobUrl = URL.createObjectURL(data);
      console.log(this.blobUrl);
    });
  }
}
