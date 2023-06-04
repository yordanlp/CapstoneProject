import { Component, OnDestroy, OnInit } from '@angular/core';
import { Observable, Subscription } from 'rxjs';
import { ImageService } from 'src/app/services/image.service';
import { AppConfig } from 'src/app/services/app-config.service';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit, OnDestroy {

  imagesObservable$: Observable<any> = null!;
  imagesSubscription: Subscription = null!;

  constructor(private imageService: ImageService) {
    this.imagesObservable$ = this.imageService.getImages();

  }
  ngOnDestroy(): void {
    this.imagesSubscription.unsubscribe();
  }
  ngOnInit(): void {
    this.imagesSubscription = this.imagesObservable$.subscribe(
      data => console.log(data)
      , error => console.error(error)
    );
  }



}
