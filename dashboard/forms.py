from django import forms

SCANNER_CHOICES = [("MCWMR02", "MCWMR02"),("MCWMR01","MCWMR01")]
COIL_CHOICES = [("RM:32NovaHeadPR", "RM:32NovaHeadPR"), ("RM:32NovaHead2", "RM:32NovaHead2"), ("21HN+60PA", "21HN+60PA"), ("21HN", "21HN"), ("48HP", "48HP"), ("48HAP", "48HAP")]
STAT_CHOICES = [("All", "All"),("mean", "mean"), ("SNR", "SNR"), ("SFNR", "SFNR"), ("std", "std"), ("percentfluc", "percentfluc"), ("drift", "drift"), ("driftfit", "driftfit"), ("driftcmassx", "driftcmassx"), ("driftcmassy", "driftcmassy"), ("driftcmassz", "driftcmassz"), ("dispcmassx","dispcmassx"),("dispcmassy","dispcmassy"),("dispcmassz","dispcmassz"), ("rdc", "rdc"), ("CMassX", "CMassX"), ("CMassY", "CMassY"), ("CMassZ", "CMassZ"), ("FWHMX", "FWHMX"), ("FWHMY", "FWHMY"), ("FWHMZ", "FWHMZ"), ("MeanGhost", "MeanGhost")]

class DailyForm(forms.Form):
    scandate = forms.CharField(required=False, max_length=100)
    scanner = forms.ChoiceField(choices=SCANNER_CHOICES,required=False)
    coil = forms.ChoiceField(choices=COIL_CHOICES, required=False)

class HistoryForm(forms.Form):
    scanner = forms.ChoiceField(choices=SCANNER_CHOICES,required=False)
    coil = forms.ChoiceField(choices=COIL_CHOICES, required=False)
    stat = forms.MultipleChoiceField(choices=STAT_CHOICES)
    daterange = forms.CharField(required=False, max_length=100)

