// OpenClaw Android Setup - DroidScript Edition
// Personality: Courteous, Empathetic, Energized!
// Performance Supply Depot LLC - For Mortimer

app.SetTitle("🤖 OpenClaw Setup");

function OnStart() {
    // Detect Android version
    var sdk = app.GetBuildNum();
    var isOld = sdk < 26;
    
    lay = app.CreateLayout("Linear", "VCenter,FillXY");
    lay.SetBackColor("#0f0f23");
    
    // Title with personality
    var title = app.CreateText("🌟 Welcome to OpenClaw!", 0.9, -1);
    title.SetTextSize(24);
    title.SetTextColor("#00d4ff");
    title.SetTextShadow(2, 2, "#000");
    lay.AddChild(title);
    
    // Subtitle
    var subtitle = app.CreateText("Your AI companion awaits...", 0.8, -1);
    subtitle.SetTextSize(14);
    subtitle.SetTextColor("#a0a0a0");
    lay.AddChild(subtitle);
    
    // Version check
    if(isOld) {
        var warning = app.CreateText("⚠️ Android " + sdk + " detected", 0.8, -1);
        warning.SetTextSize(14);
        warning.SetTextColor("#ffaa00");
        lay.AddChild(warning);
        
        var alt = app.CreateText("We'll use compatibility mode 💪", 0.8, -1);
        alt.SetTextSize(12);
        alt.SetTextColor("#888");
        lay.AddChild(alt);
    }
    
    // Progress container
    var scroll = app.CreateScroller(0.9, 0.5);
    logLay = app.CreateLayout("Linear", "FillX");
    scroll.AddChild(logLay);
    lay.AddChild(scroll);
    
    // Buttons
    var btnLay = app.CreateLayout("Linear", "Horizontal");
    
    var setupBtn = app.CreateButton("🚀 Start Setup", 0.4, 0.1);
    setupBtn.SetBackColor("#00d4ff");
    setupBtn.SetTextColor("#000");
    setupBtn.SetOnTouch(function() {
        RunSetup(isOld);
    });
    btnLay.AddChild(setupBtn);
    
    var helpBtn = app.CreateButton("💡 Help", 0.25, 0.1);
    helpBtn.SetBackColor("#16213e");
    helpBtn.SetOnTouch(ShowHelp);
    btnLay.AddChild(helpBtn);
    
    lay.AddChild(btnLay);
    
    // Status text
    status = app.CreateText("Ready to install OpenClaw! 🎉", 0.9, -1);
    status.SetTextSize(14);
    status.SetTextColor("#888");
    lay.AddChild(status);
    
    app.AddLayout(lay);
}

function RunSetup(isOld) {
    status.SetText("Starting setup... This may take a few minutes ⏳");
    
    var steps = isOld ? [
        "pkg update -y",
        "pkg install -y git nodejs-lts openssh",
        "sshd",
        "npm i -g openclaw --unsafe-perm"
    ] : [
        "pkg update -y && pkg upgrade -y",
        "pkg install -y git nodejs openssh tmux wget curl python",
        "sshd",
        "npm i -g openclaw"
    ];
    
    var current = 0;
    
    function NextStep() {
        if(current >= steps.length) {
            status.SetText("🎉 OpenClaw installed! Amazing work!");
            ShowCompletion();
            return;
        }
        
        var step = steps[current];
        status.SetText("Step " + (current+1) + "/" + steps.length + ": " + step.substring(0, 30) + "...");
        
        app.Execute(step, function(result) {
            current++;
            setTimeout(NextStep, 500);
        });
    }
    
    NextStep();
}

function ShowCompletion() {
    var dlg = app.CreateDialog("Success! 🌟");
    dlg.SetBackColor("#0f0f23");
    
    var lay = app.CreateLayout("Linear", "VCenter,FillX");
    
    var txt = app.CreateText("OpenClaw is ready!", 0.8, -1);
    txt.SetTextSize(18);
    txt.SetTextColor("#00d4ff");
    lay.AddChild(txt);
    
    var cmd = app.CreateText("Run: termux-chroot openclaw onboard", 0.9, -1);
    cmd.SetTextSize(12);
    cmd.SetTextColor("#888");
    lay.AddChild(cmd);
    
    var copyBtn = app.CreateButton("📋 Copy Command", 0.5, 0.08);
    copyBtn.SetOnTouch(function() {
        app.SetClipboardText("termux-chroot openclaw onboard");
        app.ShowPopup("Copied to clipboard! 📋");
    });
    lay.AddChild(copyBtn);
    
    var closeBtn = app.CreateButton("✅ Done", 0.3, 0.08);
    closeBtn.SetOnTouch(function() {
        dlg.Dismiss();
    });
    lay.AddChild(closeBtn);
    
    dlg.AddLayout(lay);
    dlg.Show();
}

function ShowHelp() {
    var items = [
        "📖 Documentation",
        "🔧 Fix npm errors",
        "🌐 SSH setup help", 
        "📱 Old Android tips",
        "💬 Contact support"
    ];
    
    var dlg = app.CreateListDialog("How can I help you? 😊", items);
    dlg.SetBackColor("#0f0f23");
    dlg.SetOnTouch(function(item) {
        if(item.includes("Documentation")) {
            app.OpenUrl("https://docs.openclaw.ai");
        } else if(item.includes("npm")) {
            app.Alert("Try:\nnpm cache clean --force\nnpm i -g openclaw --unsafe-perm", "npm Fix");
        } else if(item.includes("SSH")) {
            app.Execute("ifconfig", function(out) {
                var ip = out.match(/inet\s+(\d+\.\d+\.\d+\.\d+)/);
                ip = ip ? ip[1] : "Check WiFi IP";
                app.Alert("Your IP: " + ip + "\nPort: 8022\n\nConnect:\nssh user@" + ip + " -p 8022", "SSH Info");
            });
        } else if(item.includes("Android")) {
            app.Alert("For Android \u003c 8:\n\n1. Use UserLAnd app\n2. Try proot-distro\n3. Use remote server", "Compatibility");
        }
    });
    dlg.Show();
}
