{
  // data file
  TFile * f = new TFile("../data/165526/VELODQM_165526_2015-10-12_18.05.29_NZS.root");
  // sub-catalogue -- seperate for each data-set
  TString CATALOGUE("165526_mock");

  // there are 41 sensors total
  const int lastSensorId = 41;

//  TCanvas * cv = new TCanvas();

  TString sensorId;
  TString params; // [lastSensorId + 1];
  TString params_i;
  
  // histogram handles
  //TH2D* h2d;
  TH1D* noiseDistr;

  for (int i = 0; i <= lastSensorId; i++) 
  {
    TCanvas * cv = new TCanvas();
    cv->Clear();
    
    // refresh default sensor name
    TString sensorName("TELL1_000");

    // set sensor name so it corresponds to the loop index
    sensorId.Form("%d", i);
    sensorName.Replace(sensorName.Sizeof() - sensorId.Sizeof(), sensorId.Sizeof(), sensorId);
    cout << "Working on sensor: " << sensorName << endl;

    // go to sensor's location (inside the ROOT file)
    if (!(f->cd("Vetra;1/VeloPedestalSubtractorMoni/" + sensorName + ";1"))) {
      cout << "Couldn't find sensor: " << sensorName << endl;
      break;
    }
    cout << "inside the folder" << endl;
    
    // draw its few graphs and save them
    // (1) 2D histogram
    h2d = Ped_Sub_ADCs_2D;
    h2d -> DrawCopy("colz");
    //Ped_Sub_ADCs_2D.Draw("colz");

    //Ped_Sub_ADCs_2D.DrawCopy("colz");
    
    //TH2D *h2d = (TH2D*)gDirectory -> GetList() -> FindObject("Ped_Sub_ADCs_2D");
    //h2d -> Draw("colz");
    cv->SaveAs("../fig/" + CATALOGUE + "/" + sensorName + "_2D" + ".png");
    cv->Clear();

    cout << "1d hists now" << endl;

    // (2) 1D projection onto y-axis
    noiseDistr = Ped_Sub_ADCs_2D.ProjectionY(); 
    noiseDistr->DrawCopy();
    cv->SaveAs("../fig/" + CATALOGUE + "/" + sensorName + "_noiseDistr" + ".png");

    // get statistical params of the noise distribution
    double mu, sig, skew, kur, quality;
    mu = noiseDistr->GetMean();
    sig = noiseDistr->GetRMS();
    skew = noiseDistr->GetSkewness();
    kur = noiseDistr->GetKurtosis();

    // sensor quality 0 or 1 for now;
    quality = 1.0;  // assume all are OK. Otherwise, if there a few bad ones, you can adjust them manually in the output file


    params_i.Form("%f,%f,%f,%f,%f\n", mu, sig, skew, kur, quality);
    params.Append(params_i);

    // display the statistics
    cout << "Stat params {mu, sig, skewness, kurtosis} : " << endl;
    cout << params;

    cv->Clear();
  }
    //cout << params;
    ofstream myfile;
    myfile.open("../data/" + CATALOGUE + "/" + "sensorData.dat");
    myfile << params;
    myfile.close();
}
