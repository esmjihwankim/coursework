using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class MainMenuManager : MonoBehaviour
{

    public GameObject m_MainMenu;
    public GameObject m_Text;
    public GameObject m_Toggle1;
    public GameObject m_Toggle2;
    public GameObject m_Slider;

    public void Text_btn_clicked()
    {
        m_MainMenu.SetActive(false);
        m_Text_SetActive(true);
    }

    public void Text_back_clicked()
    {
        m_MainMenu.SetActive(true);
        m_Text_SetActive(false);
    }


    public void Toggle1_btn_clicked()
    {
        m_MainMenu.SetActive(false);
        m_Toggle1_SetActive(true);
    }

    public void Toggle1_back_clicked()
    {
        m_MainMenu.SetActive(true);
        m_Toggle1_SetActive(false);
    }

    public void Toggle2_btn_clicked()
    {
        m_MainMenu.SetActive(false);
        m_Toggle2_SetActive(true);
    }

    public void Toggle2_back_clicked()
    {
        m_MainMenu.SetActive(true);
        m_Toggle2_SetActive(false);
    }


    public void Slider_clicked()
    {
        m_MainMenu.SetActive(false);
        m_Slider_SetActive(true);
    }

    public void Text_back_clicked()
    {
        m_MainMenu.SetActive(true);
        m_Slider_SetActive(false);
    }


}
