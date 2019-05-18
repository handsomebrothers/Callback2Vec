package myrcpview.actions;

import org.eclipse.jface.action.Action;
import org.eclipse.jface.action.IAction;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.jface.viewers.ISelection;
import org.eclipse.ui.IPageLayout;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.IWorkbenchWindow;
import org.eclipse.ui.IWorkbenchWindowActionDelegate;
import org.eclipse.ui.PartInitException;

import myrcpview.editor.MyMulEditor;

public class MyMenu implements IWorkbenchWindowActionDelegate{
	IWorkbenchWindow window;
	@Override
	public void run(IAction action) {
		// TODO Auto-generated method stub
		//获取当前页面String editor=layout.getEditorArea();
		/*layout.addView("MySampleView.view7", IPageLayout.LEFT, 0.25f, editor);
		layout.addView("MySampleView.view9", IPageLayout.BOTTOM, 0.75f, editor);
		layout.addView("MySampleView.view8", IPageLayout.RIGHT, 0.65f, editor);*/
		IWorkbenchPage page=window.getActivePage();
		try {
			page.showView("MyRcpView.view2");
		} catch (PartInitException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
	}

	@Override
	public void selectionChanged(IAction action, ISelection selection) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void dispose() {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void init(IWorkbenchWindow window) {
		// TODO Auto-generated method stub
		this.window=window;
	}
}
