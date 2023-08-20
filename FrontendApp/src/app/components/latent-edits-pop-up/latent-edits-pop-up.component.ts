import { AfterViewInit, Component, ElementRef, EventEmitter, Input, OnInit, Output, ViewChild } from '@angular/core';
import { LatentEdit } from '../../models/latent-edit.model';

@Component({
  selector: 'app-latent-edits-pop-up',
  templateUrl: './latent-edits-pop-up.component.html',
  styleUrls: ['./latent-edits-pop-up.component.css']
})
export class LatentEditsPopUpComponent implements OnInit, AfterViewInit{

  @ViewChild('modalDialog', { static: false }) modalDialog!: ElementRef<HTMLDialogElement>;
  latentEdit: LatentEdit;
  interpolationSteps: number = 1;
  latentEdits: Array<LatentEdit> = Array();
  @Output() updateLatentEdits = new EventEmitter<{
      interpolationSteps: number
      latentEdits: Array<LatentEdit>
  }>();

  @Output() close = new EventEmitter<any>();

  constructor() {
    this.latentEdit = {
      principal_component_number: 0,
      start_layer: 0,
      end_layer: 0,
      lower_coeff_limit: 0,
      upper_coeff_limit: 0
    }
  }
  ngAfterViewInit(): void {
  }
  showModal(){
    this.latentEdit = {
      principal_component_number: 0,
      start_layer: 0,
      end_layer: 0,
      lower_coeff_limit: 0,
      upper_coeff_limit: 0
    }
    this.modalDialog.nativeElement.showModal();
  }

  submitLatentEdits(){
    console.log("Latent Edits", this.latentEdits);
    this.updateLatentEdits.emit({
      interpolationSteps: this.interpolationSteps,
      latentEdits: this.latentEdits
    });
    this.latentEdit = {
      principal_component_number: 0,
      start_layer: 0,
      end_layer: 0,
      lower_coeff_limit: 0,
      upper_coeff_limit: 0
    }
    this.latentEdits = [];
    this.interpolationSteps = 1;
    this.closeModal();
  }

  addLatentEdit(): void {
    this.latentEdits.push({
      principal_component_number: this.latentEdit.principal_component_number,
      start_layer: this.latentEdit.start_layer,
      end_layer: this.latentEdit.end_layer,
      lower_coeff_limit: this.latentEdit.lower_coeff_limit,
      upper_coeff_limit: this.latentEdit.upper_coeff_limit
    });
  }


  deleteLatentEdit( index: number ): void{
    if( index >= 0 && index <= this.latentEdits.length )
      this.latentEdits.splice(index, 1);
  }

  closeModal(){
    this.modalDialog.nativeElement.close();
    this.close.emit();
  }

  ngOnInit(): void {
    
  }

}
