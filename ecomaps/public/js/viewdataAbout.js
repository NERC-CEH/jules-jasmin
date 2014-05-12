function ViewdataAbout() {

    /**
     * Creates the about page.
     */
    this.createPage = function(text) {
        this.aboutPage = new Ext.Panel({
            title: 'About',
            id: 'vd-about',
            border: true,
            frame: true,
            html: text
        })
    };
}
