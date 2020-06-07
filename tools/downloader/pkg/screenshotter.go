// Command screenshot is a chromedp example demonstrating how to take a
// screenshot of a specific element and of the entire browser viewport.

package pkg

import (
	"context"
	"io/ioutil"
	"math"

	"github.com/chromedp/cdproto/emulation"
	"github.com/chromedp/cdproto/page"
	"github.com/chromedp/chromedp"
)

/*
copied from and modified from https://github.com/chromedp/examples/blob/master/screenshot/main.go
*/

func capture(url string, name string) error {
	// create context
	ctx, cancel := chromedp.NewContext(context.Background())
	defer cancel()

	// capture screenshot of an element
	var buf []byte
	if err := chromedp.Run(ctx, elementScreenshot(url, `#main`, &buf)); err != nil {
		return err
	}
	if err := ioutil.WriteFile(name+"-elementScreenshot.png", buf, 0644); err != nil {
		return err
	}

	// capture entire browser viewport, returning png with quality=90
	if err := chromedp.Run(ctx, fullScreenshot(url, 10, &buf)); err != nil {
		return err
	}
	if err := ioutil.WriteFile(name+"-fullScreenshot.png", buf, 0644); err != nil {
		return err
	}
	return nil
}

// elementScreenshot takes a screenshot of a specific element.
func elementScreenshot(urlstr, sel string, res *[]byte) chromedp.Tasks {
	return chromedp.Tasks{
		chromedp.Navigate(urlstr),
		chromedp.WaitVisible(sel, chromedp.ByID),
		chromedp.Screenshot(sel, res, chromedp.NodeVisible, chromedp.ByID),
	}
}

// fullScreenshot takes a screenshot of the entire browser viewport.
//
// Liberally copied from puppeteer's source.
//
// Note: this will override the viewport emulation settings.
func fullScreenshot(urlstr string, quality int64, res *[]byte) chromedp.Tasks {
	return chromedp.Tasks{
		chromedp.Navigate(urlstr),
		chromedp.ActionFunc(func(ctx context.Context) error {
			// get layout metrics
			_, _, contentSize, err := page.GetLayoutMetrics().Do(ctx)
			if err != nil {
				return err
			}

			width, height := int64(math.Ceil(contentSize.Width)), int64(math.Ceil(contentSize.Height))

			// force viewport emulation
			err = emulation.SetDeviceMetricsOverride(width, height, 1, false).
				WithScreenOrientation(&emulation.ScreenOrientation{
					Type:  emulation.OrientationTypePortraitPrimary,
					Angle: 0,
				}).
				Do(ctx)
			if err != nil {
				return err
			}

			// capture screenshot
			*res, err = page.CaptureScreenshot().
				WithQuality(quality).
				WithClip(&page.Viewport{
					X:      contentSize.X,
					Y:      contentSize.Y,
					Width:  contentSize.Width,
					Height: contentSize.Height,
					Scale:  1,
				}).Do(ctx)
			if err != nil {
				return err
			}
			return nil
		}),
	}
}
