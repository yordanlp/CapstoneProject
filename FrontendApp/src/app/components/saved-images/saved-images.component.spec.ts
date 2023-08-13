import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SavedImagesComponent } from './saved-images.component';

describe('SavedImagesComponent', () => {
  let component: SavedImagesComponent;
  let fixture: ComponentFixture<SavedImagesComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [SavedImagesComponent]
    });
    fixture = TestBed.createComponent(SavedImagesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
