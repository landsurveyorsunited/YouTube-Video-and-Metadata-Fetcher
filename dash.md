# DASH

YouTube uses the DASH protocol to serice is users with videos.

Pros and cons of HTTP crap
Can be used with normal HTTP servers?
DASH makes it convenient to provide media content to users since it enables content delivery from standard HTTP servers to HTTP clients. HTTP provides reliable transfer of data, and enables caching of content by standard HTTP caches. Since DASH is using HTTP as a transport protocol it inherits many advanced features such as redirection, authentication, traversing of NATs/firewalls, and TLS. Media resources are referred to by using HTTP URLs, this provides a unique location for the resources, and a simple and well-tested (?) method of accessing the resources using HTTP GET and HTTP partial GET requests.


One of the core features of DASH is the ability to request different qualities for each video. For many YouTube videos you can choose from a range of qualities between 122p and 1080p. Recently, YouTube also added 4k videos.

This is an example of a Representation of a 1080p mp4 video.
The @id field specifies an identifier for this Representation, it's used to do what exactly? Each id is linked with a specific type of video. 137 is always a 1920x1080 mp4 video, for example [https://github.com/rg3/youtube-dl/blob/master/youtube_dl/extractor/youtube.py].

The @codecs field shall specify the codecs present with this Representation. The field should also include the profile and level information where applicable. For this video, the codec specifies a H.264/AVC video, High Profile, Level 40 (fix).

The @width and @height fields specifies the resolution of the video in pixels (not the ISO DASH definition, but always true for youtube videos?).

TODO: describe SAP

@maxPlayoutRate specifies the maximum playout rate as a multiple of the regular playout rate, in this example it is set to 1, which means that it's not supported on any level.

The @bandwidth field is a little more complicated than the other fields. 
If a Representation is continuously delivered at this bitrate (in a constant bitrate channel of @bandwidth bps), starting at SAP 1, a client can be assured of having enough data for continuous playout providing playout begins after @minBufferTime * @bandwidth bits have been received.
If you consider the value to be bits per second in a channel with constant bitrate, 

Not all identifiers are specified in the ISO DASH standard. YouTube provides some of its own, and these are prefixed with yt:. One example is the @yt:contentLength field. This specifies the size of the Representation in bytes. So the total download size of the Representation will match this value.

BaseURL contains the contentLength and a HTTP URL to be used as a base URL for the Representation.

When switching between different qualities, the base URL is used together with content length and stuff to start downloading at the correct loaction for the next Representation.
*super pr0 description here*


```
{
	"@id": "137",
		"@codecs": "avc1.640028",
		"@width": "1920",
		"@height": "1080",
		"@startWithSAP": "1",
		"@maxPlayoutRate": "1",
		"@bandwidth": "4133205",
		"@frameRate": "24",
		"BaseURL": {
			"@yt:contentLength": "148765820",
			"#text": "http://r8---sn-uxaxovg-vnad.googlevideo.com/videoplayback?id=9d3e9e6819bcd9b4&itag=137&source=youtube&ms=au&pl=22&mv=m&mn=sn-uxaxovg-vnad&mm=31&ratebypass=yes&mime=video/mp4&gir=yes&clen=148765820&lmt=1443591699166739&dur=531.864&fexp=9405989,9408209,9408710,9414764,9414930,9415870,9416126,9416179,9416984,9417132,9417707,9420934,9421175,9422460,9422592,9422596,9422674,9422867,9423429&sver=3&key=dg_yt0&upn=rTJyK8MSOVI&signature=466BA9528939E220DBE518CD8F8D00C971D3D818.0D8F0B72BC71EDC25B5CDFC9285B6A182811F218&mt=1446290848&ip=95.34.86.97&ipbits=0&expire=1446312558&sparams=ip,ipbits,expire,id,itag,source,ms,pl,mv,mn,mm,ratebypass,mime,gir,clen,lmt,dur"
		},
		"SegmentBase": {
			"@indexRange": "711-1942",
			"@indexRangeExact": "true",
			"Initialization": {
				"@range": "0-710"
			}
		}
}
```


### Links
http caching: https://developers.google.com/web/fundamentals/performance/optimizing-content-efficiency/http-caching?hl=en
RFC6381: https://tools.ietf.org/html/rfc6381
https://en.wikipedia.org/wiki/ISO_8601#Durations
https://tech.ebu.ch/docs/events/webinar043-mpeg-dash/presentations/ebu_mpeg-dash_webinar043.pdf
http://www.w3.org/2010/11/web-and-tv/papers/webtv2_submission_64.pdf